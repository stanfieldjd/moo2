// Bulk pseudo-C export for the MOO2 v1.31 reverse-engineering workbench.
// @category MOO2
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;

public class ExportDecompiledFunctions extends GhidraScript {
    private static String safeName(String s) {
        return s.replaceAll("[^A-Za-z0-9_.-]", "_");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("output directory required");
        Path out = Paths.get(args[0]);
        Files.createDirectories(out);
        Path manifest = out.resolve("functions.tsv");
        DecompInterface decomp = new DecompInterface();
        decomp.toggleCCode(true);
        decomp.toggleSyntaxTree(true);
        if (!decomp.openProgram(currentProgram)) throw new IOException("decompiler could not open program");
        try (BufferedWriter index = Files.newBufferedWriter(manifest, StandardCharsets.UTF_8)) {
            index.write("entry\tname\tstatus\tfile\n");
            FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
            while (funcs.hasNext() && !monitor.isCancelled()) {
                Function f = funcs.next();
                String entry = f.getEntryPoint().toString();
                String file = entry + "__" + safeName(f.getName()) + ".c";
                DecompileResults r = decomp.decompileFunction(f, 120, monitor);
                if (r.decompileCompleted() && r.getDecompiledFunction() != null) {
                    Files.writeString(out.resolve(file), r.getDecompiledFunction().getC(), StandardCharsets.UTF_8);
                    index.write(entry + "\t" + f.getName() + "\tok\t" + file + "\n");
                } else {
                    index.write(entry + "\t" + f.getName() + "\tfailed\t\n");
                }
            }
        } finally {
            decomp.dispose();
        }
    }
}
